def calculate_bayes_rain():
    print("--- Bayes' Rule for Rain Prediction ---")

    try:
        # Taking inputs from the user
        p_cloudy = float(input("Enter probability of it being cloudy P(Cloudy) [0-1]: "))
        p_rain = float(input("Enter probability of rain P(Rain) [0-1]: "))
        p_cloudy_given_rain = float(input("Enter probability of clouds on a rainy day P(Cloudy|Rain) [0-1]: "))

        # Bayes' Rule Formula: P(A|B) = [P(B|A) * P(A)] / P(B)
        # P(Rain|Cloudy) = [P(Cloudy|Rain) * P(Rain)] / P(Cloudy)

        p_rain_given_cloudy = (p_cloudy_given_rain * p_rain) / p_cloudy

        # Displaying results
        print(f"\nResults:")
        print(f"Probability of rain given it is cloudy P(Rain|Cloudy): {p_rain_given_cloudy:.4f}")
        print(f"Percentage: {p_rain_given_cloudy * 100:.2f}%")

    except ZeroDivisionError:
        print("Error: Probability of cloudy cannot be zero.")
    except ValueError:
        print("Error: Please enter valid numerical values between 0 and 1.")

if __name__ == "__main__":
    calculate_bayes_rain()
