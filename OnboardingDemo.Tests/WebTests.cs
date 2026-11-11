using System.Text.Json;

namespace OnboardingDemo.Tests;

public class WebTests
{
    private static readonly TimeSpan DefaultTimeout = TimeSpan.FromMinutes(3);

    [Fact]
    public async Task ApplicationServesFrontendAndForecastWithHealthyDependencies()
    {
        using var timeout = new CancellationTokenSource(DefaultTimeout);
        var cancellationToken = timeout.Token;

        var appHost = await DistributedApplicationTestingBuilder.CreateAsync<Projects.OnboardingDemo_AppHost>(cancellationToken);
        appHost.Services.ConfigureHttpClientDefaults(clientBuilder =>
        {
            clientBuilder.AddStandardResilienceHandler();
        });

        await using var app = await appHost.BuildAsync(cancellationToken).WaitAsync(DefaultTimeout, cancellationToken);
        await app.StartAsync(cancellationToken).WaitAsync(DefaultTimeout, cancellationToken);

        await app.ResourceNotifications.WaitForResourceHealthyAsync("cache", cancellationToken);
        await app.ResourceNotifications.WaitForResourceHealthyAsync("apiservice", cancellationToken);
        await app.ResourceNotifications.WaitForResourceHealthyAsync("webfrontend", cancellationToken);

        using var webClient = app.CreateHttpClient("webfrontend");
        using var apiClient = app.CreateHttpClient("apiservice");

        var home = await webClient.GetStringAsync("/", cancellationToken);
        Assert.Contains("Welcome to the team!", home);

        var firstResponse = await apiClient.GetStringAsync("/weatherforecast", cancellationToken);
        var cachedResponse = await apiClient.GetStringAsync("/weatherforecast", cancellationToken);
        Assert.Equal(firstResponse, cachedResponse);

        var forecast = JsonSerializer.Deserialize<JsonElement[]>(firstResponse);
        Assert.NotNull(forecast);
        Assert.Equal(5, forecast.Length);
        foreach (var day in forecast)
        {
            Assert.True(day.GetProperty("date").TryGetDateTime(out _));
            Assert.InRange(day.GetProperty("temperatureC").GetInt32(), -20, 54);
            Assert.Equal(
                32 + (int)(day.GetProperty("temperatureC").GetInt32() / 0.5556),
                day.GetProperty("temperatureF").GetInt32());
            Assert.False(string.IsNullOrWhiteSpace(day.GetProperty("summary").GetString()));
        }

        var weather = await webClient.GetStringAsync("/weather", cancellationToken);
        Assert.Contains("<table", weather);
        Assert.Contains("Redis", weather);
        Assert.DoesNotContain("An unhandled exception", weather);

        using var webHealth = await webClient.GetAsync("/health", cancellationToken);
        using var apiHealth = await apiClient.GetAsync("/health", cancellationToken);
        Assert.Equal(HttpStatusCode.OK, webHealth.StatusCode);
        Assert.Equal(HttpStatusCode.OK, apiHealth.StatusCode);
    }
}
