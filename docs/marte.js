// MarsOS - relogio marciano do site (mesmo algoritmo Mars24 do comando `sol`)
(function () {
  "use strict";

  var TT_UTC = 69.184;
  var PBS = [
    [0.0071, 2.2353, 49.409], [0.0057, 2.7543, 168.173], [0.0039, 1.1177, 191.837],
    [0.0037, 15.7866, 21.736], [0.0021, 2.1354, 15.704], [0.0020, 2.4694, 95.528],
    [0.0018, 32.8493, 49.095]
  ];
  var LOCAIS = [["Gale (Curiosity)", 137.4417], ["Jezero (Perseverance)", 77.4509], ["Olympus Mons", 226.2]];
  var rad = Math.PI / 180;

  function calcular(ms) {
    var jdTT = 2440587.5 + ms / 86400000 + TT_UTC / 86400;
    var dt = jdTT - 2451545.0;
    var M = ((19.3871 + 0.52402073 * dt) % 360) * rad;
    var alfa = (270.3871 + 0.524038496 * dt) % 360;
    var pbs = 0;
    PBS.forEach(function (p) { pbs += p[0] * Math.cos((0.985626 * dt / p[1] + p[2]) * rad); });
    var eqc = (10.691 + 3e-7 * dt) * Math.sin(M) + 0.623 * Math.sin(2 * M) + 0.050 * Math.sin(3 * M) +
              0.005 * Math.sin(4 * M) + 0.0005 * Math.sin(5 * M) + pbs;
    var ls = ((alfa + eqc) % 360 + 360) % 360;
    var msd = (jdTT - 2405522.0028779) / 1.0274912517;
    var mtc = ((24 * msd) % 24 + 24) % 24;
    var ano = 36 + Math.round(((msd - 52292.88) - (ls / 360) * 668.5921) / 668.5921);
    return { msd: msd, mtc: mtc, ls: ls, ano: ano };
  }

  function hms(h) {
    var s = Math.round((((h % 24) + 24) % 24) * 3600) % 86400;
    function d(n) { return (n < 10 ? "0" : "") + n; }
    return d(Math.floor(s / 3600)) + ":" + d(Math.floor(s % 3600 / 60)) + ":" + d(s % 60);
  }
  function milhar(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, "."); }
  var NORTE = ["Primavera", "Verão", "Outono", "Inverno"];
  var SUL = ["Outono", "Inverno", "Primavera", "Verão"];

  function pad(rotulo) { var s = rotulo + " "; while (s.length < 26) s += "."; return s; }

  function atualizar() {
    var agora = Date.now();
    var m = calcular(agora);
    var est = Math.floor(m.ls / 90) % 4;
    var sol = milhar(Math.floor(m.msd));

    var mini = document.getElementById("mini-sol");
    if (mini) {
      mini.innerHTML = "<b>SOL " + sol + "</b><span>MTC " + hms(m.mtc).slice(0, 5) + "</span>";
    }
    var term = document.getElementById("terminal-sol");
    if (term) {
      var linhas = [
        '<span class="p">astronauta@marte</span>:<span class="h">~</span>$ sol',
        "",
        '  <span class="p">MarsOS · Relógio Marciano</span>',
        '  <span class="a">────────────────────────────────────────────</span>',
        '  <span class="a">' + pad("Sol marciano (MSD)") + '</span> <span class="h">' + sol + "</span>  (" + m.msd.toFixed(4) + ")",
        '  <span class="a">' + pad("Hora coordenada (MTC)") + '</span> <span class="h">' + hms(m.mtc) + "</span>",
        '  <span class="a">' + pad("Ano marciano") + "</span> " + m.ano,
        '  <span class="a">' + pad("Longitude solar (Ls)") + "</span> " + m.ls.toFixed(1).replace(".", ",") + "°",
        '  <span class="a">' + pad("Estação") + "</span> " + NORTE[est] + " no norte · " + SUL[est] + " no sul"
      ];
      LOCAIS.forEach(function (l) {
        linhas.push('  <span class="a">' + pad(l[0]) + "</span> " + hms(m.mtc + l[1] / 15).slice(0, 5) + " (hora local)");
      });
      linhas.push('  <span class="a">' + pad("Terra (UTC)") + "</span> " +
        new Date(agora).toISOString().replace("T", " ").slice(0, 19));
      linhas.push("", '<span class="p">astronauta@marte</span>:<span class="h">~</span>$ <span class="cursor"></span>');
      term.innerHTML = linhas.join("\n");
    }
    var relogio = document.getElementById("hora-terra");
    if (relogio) {
      var d = new Date(agora);
      relogio.textContent = (d.getHours() < 10 ? "0" : "") + d.getHours() + ":" + (d.getMinutes() < 10 ? "0" : "") + d.getMinutes();
    }
  }

  // som de inicializacao
  var botaoSom = document.getElementById("tocar-som");
  if (botaoSom) {
    var audio = new Audio("img/inicio.wav");
    botaoSom.addEventListener("click", function () {
      audio.currentTime = 0;
      audio.play();
    });
  }

  atualizar();
  setInterval(atualizar, 1000);
})();
