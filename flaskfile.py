from flask import Flask, request, render_template
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)


# Define the Flask route for the homepage
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Fetch user input from the form
        variant_a_users = int(request.form["variant_a_users"])
        variant_a_bookings = int(request.form["variant_a_bookings"])
        variant_b_users = int(request.form["variant_b_users"])
        variant_b_bookings = int(request.form["variant_b_bookings"])

        # Bayesian A/B test parameters
        alpha_prior = 1  # Prior successes
        beta_prior = 1  # Prior failures

        # Calculate posterior parameters
        alpha_a_post = alpha_prior + variant_a_bookings
        beta_a_post = beta_prior + variant_a_users - variant_a_bookings

        alpha_b_post = alpha_prior + variant_b_bookings
        beta_b_post = beta_prior + variant_b_users - variant_b_bookings

        # Monte Carlo sampling
        samples = 100000
        p_a = np.random.beta(alpha_a_post, beta_a_post, samples)
        p_b = np.random.beta(alpha_b_post, beta_b_post, samples)

        # Probability that Variant B is better than Variant A
        prob_b_better_than_a = np.mean(p_b > p_a)

        # Generate plot
        x = np.linspace(0, 1, 1000)
        plt.figure(figsize=(10, 5))
        plt.plot(x, stats.beta.pdf(x, alpha_a_post, beta_a_post), label="Variant A")
        plt.plot(x, stats.beta.pdf(x, alpha_b_post, beta_b_post), label="Variant B")
        plt.title("Posterior Distributions for Conversion Rates")
        plt.xlabel("Conversion Rate")
        plt.ylabel("Density")
        plt.legend()

        # Save plot to a string buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        buf.close()

        # Return results to the webpage
        return render_template(
            "index.html",
            prob_b_better_than_a=round(prob_b_better_than_a * 100, 2),
            image_base64=image_base64,
        )

    # Render the form on GET request
    return render_template("index.html")


# Run the application
if __name__ == "__main__":
    app.run(debug=True)