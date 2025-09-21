fetch('/api/top10')
  .then(response => response.json())
  .then(data => {
    const list = document.getElementById('track-list');
    data.tracks.forEach(track => {
      const item = document.createElement('li');

      const img = document.createElement('img');
      img.src = track.album_cover;
      img.alt = `${track.song_name} album cover`;
      img.className = 'album-cover';

      const name = document.createElement('div');
      name.textContent = track.song_name;
      name.className = 'track-name';

      const artist = document.createElement('div');
      artist.textContent = track.artists;
      artist.className = 'artist-name';

      item.appendChild(img);
      item.appendChild(name);
      item.appendChild(artist);
      list.appendChild(item);
    });
  });