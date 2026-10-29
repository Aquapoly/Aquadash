/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,ts}"],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        light: {
          ...require("daisyui/src/theming/themes")["light"],
          primary: "#65c3c8",
          "primary-content": "#223D30",
          secondary: "#66cc8a",
          "secondary-content": "#fff",
        },
      },
      ,
      {
        dracula: {
          ...require("daisyui/src/theming/themes")["dracula"],
          primary: "#1DB88E",
          secondary: "#3ac26c",
        },
      },
    ],
  },
};
