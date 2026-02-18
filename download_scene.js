// This script runs in the browser console to save image data to a global var
// Then we extract in chunks via evaluate calls

async function downloadGrokImage(url) {
  const r = await fetch(url, {credentials: 'include'});
  const b = await r.blob();
  const reader = new FileReader();
  return new Promise(res => {
    reader.onloadend = () => {
      window.__imgBase64 = reader.result.split(',')[1];
      res(window.__imgBase64.length);
    };
    reader.readAsDataURL(b);
  });
}
