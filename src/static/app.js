document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message and reset activity select
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Build participants section (styled list with delete buttons)
        let participantListHTML = "";
        if (Array.isArray(details.participants) && details.participants.length > 0) {
          participantListHTML = `<ul class=\"participants-list\">` +
            details.participants.map(p => `<li><span class=\"participant-email\">${p}</span> <button class=\"participant-delete\" data-activity=\"${name}\" data-email=\"${p}\" title=\"Unregister\">✕</button></li>`).join("") +
            `</ul>`;
        } else {
          participantListHTML = `<p class=\"no-participants\">No participants yet</p>`;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants">
            <h5>Participants (${details.participants ? details.participants.length : 0})</h5>
            ${participantListHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);

        // Attach delete handlers for participants in this card
        activityCard.querySelectorAll(".participant-delete").forEach(btn => {
          btn.addEventListener("click", async (e) => {
            const email = btn.dataset.email;
            const activityName = btn.dataset.activity;
            if (!confirm(`Unregister ${email} from ${activityName}?`)) return;
            try {
              const res = await fetch(`/activities/${encodeURIComponent(activityName)}/signup?email=${encodeURIComponent(email)}`, { method: "DELETE" });
              const result = await res.json();
              if (res.ok) {
                // refresh activities UI
                fetchActivities();
                messageDiv.textContent = result.message;
                messageDiv.className = "success";
              } else {
                messageDiv.textContent = result.detail || "Failed to unregister";
                messageDiv.className = "error";
              }
            } catch (err) {
              messageDiv.textContent = "Failed to unregister. Try again.";
              messageDiv.className = "error";
              console.error(err);
            } finally {
              messageDiv.classList.remove("hidden");
              setTimeout(() => { messageDiv.classList.add("hidden"); }, 5000);
            }
          });
        });
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    const submitBtn = signupForm.querySelector("button[type='submit']");
    submitBtn.disabled = true;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities so the new participant appears immediately
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      console.error("Error signing up:", error);
    } finally {
      submitBtn.disabled = false;
      messageDiv.classList.remove("hidden");
      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    }
  });

  // Initialize app
  fetchActivities();
});
