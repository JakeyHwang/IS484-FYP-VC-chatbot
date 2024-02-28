export const metadata = {
  title: "VerChat",
  description: "Verbot by Vertex",
};

export default function RootLayout({ children }) {
  return (
    <>
      <html lang="en">
        <body>{children}</body>
      </html>
    </>
  );
}
