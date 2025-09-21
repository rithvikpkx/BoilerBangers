// fetch('/api/top10')
//   .then(response => response.json())
//   .then(data => {
//     const list = document.getElementById('track-list');
//     data.tracks.forEach(track => {
//       const item = document.createElement('li');
//       item.textContent = `${track.song_name} by ${track.artists} — ${track.points} points`;
//       list.appendChild(item);
//     });
//   });


fetch('/api/top10')
  .then(response => response.json())
  .then(data => {
    const list = document.getElementById('track-list');
    data.tracks.forEach(track => {
      const item = document.createElement('li');
      item.textContent = `${track.song_name} by ${track.artists} — ${track.points} points`;
      list.appendChild(item);
    });
  });