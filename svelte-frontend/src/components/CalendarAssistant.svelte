<script>
  import { onMount, onDestroy } from 'svelte';
  import { Calendar } from '@fullcalendar/core';
  import dayGridPlugin from '@fullcalendar/daygrid';
  import interactionPlugin from '@fullcalendar/interaction';
  import listPlugin from '@fullcalendar/list';

  export let appointments = [];

  let calendar;

  onMount(() => {
    const calendarEl = document.getElementById('calendar');
    calendar = new Calendar(calendarEl, {
      plugins: [dayGridPlugin, interactionPlugin, listPlugin],
      initialView: 'dayGridMonth',
      weekends: false
    });

    calendar.render();
    return () => {
      calendar.destroy();
    };
  });

  $: if (calendar) {
    calendar.removeAllEvents();
    calendar.addEventSource(appointments.map(app => ({
      title: app.title,
      start: app.start_time,
      end: app.end_time,
      extendedProps: { description: app.description }
    })));
  }
</script>

<div id="calendar"></div>
