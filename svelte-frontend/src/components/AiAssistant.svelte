<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  import CalendarAssistant from './CalendarAssistant.svelte';

  let action = '';
  let userFriendlyMessage = '';
  let appointments = [];
  let loading = false;
  let showCalendar = false;
  let showAppointmentForm = false;

  let employeeId = '';
  let title = '';
  let description = '';
  let startTime = '';
  let endTime = '';

  let recording = false;
  let mediaRecorder;
  let audioChunks = [];
  let audioBlob;

  // Function to handle form submission for generating messages or determining intent
  const generateMessage = async () => {
    loading = true;
    userFriendlyMessage = '';
    try {
      const response = await fetch('http://localhost:8000/generate-message/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });
      const data = await response.json();
      loading = false;

      if (data.appointments) {
        appointments = data.appointments;
        showCalendar = true;
        showAppointmentForm = false;
      } else if (data.intent === 'booking') {
        showAppointmentForm = true;
        showCalendar = false;
      } else {
        userFriendlyMessage = data.user_friendly_message;
				showCalendar = false;
        showAppointmentForm = false;
      }
    } catch (error) {
      console.error('Error:', error);
      userFriendlyMessage = "Failed to load data, please try again.";
      loading = false;
    }
  };

  // Function to create a new appointment
  async function createAppointment() {
    loading = true;
    try {
      const response = await fetch('http://localhost:8000/create-appointment/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          employee_id: employeeId, // Ensure this is included
          title,
          description,
          start_time: startTime,
          end_time: endTime
        })
      });
      const data = await response.json();
      if (data.appointment) {
        appointments.push(data.appointment);
        showCalendar = true;
        showAppointmentForm = false;
        userFriendlyMessage = "Appointment created successfully.";
      } else {
        userFriendlyMessage = data.error || "Failed to create appointment.";
      }
      loading = false;
    } catch (error) {
      console.error('Error:', error);
      userFriendlyMessage = "Failed to create appointment.";
      loading = false;
    }
  }

  const startRecording = async () => {
    audioChunks = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = event => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      transcribeAudio(audioBlob);
    };

    mediaRecorder.start();
    recording = true;
  };

  const stopRecording = () => {
    mediaRecorder.stop();
    recording = false;
  };

  const transcribeAudio = async (audioBlob) => {
    loading = true;
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'audio.wav');

      const response = await axios.post('http://localhost:8000/transcribe/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });

      action = response.data.text; // Paste the transcribed text into the action input
      loading = false;
    } catch (error) {
      console.error('Error:', error);
      userFriendlyMessage = "Failed to transcribe audio, please try again.";
      loading = false;
    }
  };
</script>

<main>
  <h1>Determine Intent of Personal</h1>

  <form on:submit|preventDefault={generateMessage}>
    <label>
      <span>Action:</span>
      <input type="text" bind:value={action} required />
      <div class="buttons">
        <button type="button" on:click={startRecording} disabled={recording || loading}>
          Start Recording
        </button>
        <button type="button" on:click={stopRecording} disabled={!recording || loading}>
          Stop Recording
        </button>
      </div>
    </label>

    <button type="submit" disabled={loading}>
      <span>{loading ? 'Loading...' : 'Generate Message'}</span>
      {#if loading}
        <div class="loader"></div>
      {/if}
    </button>
  </form>

  {#if showAppointmentForm}
    <div>
      <input type="number" bind:value={employeeId} placeholder="Employee ID" required />
      <input type="text" bind:value={title} placeholder="Title" required />
      <input type="text" bind:value={description} placeholder="Description" />
      <input type="datetime-local" bind:value={startTime} required />
      <input type="datetime-local" bind:value={endTime} required />
      <button on:click={createAppointment} disabled={loading}>Create Appointment</button>
    </div>
  {/if}
  {#if showCalendar && appointments.length > 0}
    <CalendarAssistant {appointments} />
  {:else if userFriendlyMessage}
    <div class="result">
      <h2>User-Friendly Message:</h2>
      <p>{userFriendlyMessage}</p>
    </div>
  {/if}
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 600px;
		margin: 0 auto;
	}

	form {
		display: grid;
		gap: 1em;
		margin-bottom: 1em;
	}

	label {
		display: block;
		text-align: left;
	}

	input {
		width: 100%;
		padding: 0.5em;
		font-size: 1em;
		border: 1px solid #ccc;
		border-radius: 0.5em;
	}

	button {
		padding: 0.5em 1em;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1em;
		background-color: #007bff;
		color: #fff;
		border: none;
		border-radius: 0.5em;
		cursor: pointer;
		position: relative;
		overflow: hidden;
		transition: background-color 0.3s;
	}

  .buttons {
    display: flex;
    justify-content: space-between;
  }

	button:hover {
		background-color: #0056b3;
	}

	.loader {
		transform: translate(-50%, -50%);
		border: 4px solid #254668;
		border-top: 4px solid #3498db;
		border-radius: 50%;
		margin-left: 15px;
		width: 20px;
		height: 20px;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	.result {
		margin-top: 2em;
		text-align: left;
	}

	h2 {
		margin-top: 1.5em;
	}

	p {
		margin-bottom: 1em;
	}
</style>
