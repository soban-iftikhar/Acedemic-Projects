const FLAGS = {
  sqli: "flag{sql_1nj3ct10n_byp4ss_m4st3r}",
  idor: "flag{1d0r_pr0f1l3_3num3r4t10n}",
  xss: "flag{xss_scr1pt_1nj3ct3d_c00k13}",
  bac: "flag{br0k3n_4cc3ss_4dm1n_p4n3l}",
  crypto: "flag{c4es4r_c1ph3r_r0t13_cr4ck3d}",
  hash: "flag{md5_h4sh_cr4ck3d_3z}",
  rsa: "flag{rs4_pr1v4t3_k3y_d3crypt3d}",
  bruteforce: "flag{br0t3_f0rc3_w34k_p4ssw0rd}",
  diffie: "flag{d1ff13_h3llm4n_k3y_3xch4ng3}",
  vigenere: "flag{v1g3n3r3_c1ph3r_cr4ck3d}"
};

const CRYPTO_ENCODED = "synt{p4rf4e_p1cu3e_e0g13_pe4px3q}";

const CHALLENGE_SEED = [
  {
    slug: "sqli",
    title: "Login Bypass",
    category: "Injection",
    difficulty: "Easy",
    points: 100,
    description:
      "A legacy login portal was deployed without proper input sanitization. Bypass authentication using SQL injection.",
    hint: "Try closing the string and forcing true logic.",
    hintCost: 30,
    flag: FLAGS.sqli
  },
  {
    slug: "idor",
    title: "Profile Viewer",
    category: "Broken Access Control",
    difficulty: "Easy",
    points: 100,
    description:
      "User profile IDs are exposed in the URL. Find admin secret data.",
    hint: "Admin account is usually first seeded user.",
    hintCost: 30,
    flag: FLAGS.idor
  },
  {
    slug: "xss",
    title: "Message Board",
    category: "XSS",
    difficulty: "Medium",
    points: 200,
    description:
      "Stored XSS in a shared message board. Retrieve the flag cookie.",
    hint: "Use document.cookie in a script payload.",
    hintCost: 40,
    flag: FLAGS.xss
  },
  {
    slug: "bac",
    title: "Secret Admin Panel",
    category: "Broken Access Control",
    difficulty: "Easy",
    points: 100,
    description:
      "Admin endpoint exists but backend role check is missing.",
    hint: "Try /api/challenges/bac/secret-panel directly.",
    hintCost: 30,
    flag: FLAGS.bac
  },
  {
    slug: "crypto",
    title: "Encoded Message",
    category: "Cryptography",
    difficulty: "Hard",
    points: 300,
    description:
      "Decode a ROT13-encoded transmission.",
    hint: "ROT13 shifts letters by 13.",
    hintCost: 50,
    flag: FLAGS.crypto
  },
  {
    slug: "hash",
    title: "Hash Cracking",
    category: "Cryptography",
    difficulty: "Medium",
    points: 200,
    description:
      "Crack MD5 hash 5f4dcc3b5aa765d61d8327deb882cf99.",
    hint: "This hash maps to a very common password.",
    hintCost: 40,
    flag: FLAGS.hash
  },
  {
    slug: "rsa",
    title: "RSA Decryption",
    category: "Cryptography",
    difficulty: "Hard",
    points: 300,
    description:
      "Given p=61, q=53, e=17, ciphertext=2557, recover plaintext.",
    hint: "Compute d, then use ciphertext^d mod n.",
    hintCost: 50,
    flag: FLAGS.rsa
  },
  {
    slug: "bruteforce",
    title: "Brute Force Login",
    category: "Authentication",
    difficulty: "Medium",
    points: 200,
    description:
      "No lockout and weak password list. Guess the right password.",
    hint: "The right answer is in the common password list.",
    hintCost: 40,
    flag: FLAGS.bruteforce
  },
  {
    slug: "diffie",
    title: "Diffie-Hellman Exchange",
    category: "Cryptography",
    difficulty: "Hard",
    points: 300,
    description:
      "Compute shared secret from public and private values.",
    hint: "shared = B^a mod p",
    hintCost: 50,
    flag: FLAGS.diffie
  },
  {
    slug: "vigenere",
    title: "Vigenere Cipher",
    category: "Cryptography",
    difficulty: "Medium",
    points: 200,
    description:
      "Decrypt ciphertext RIJVS{j4g3u3t3_m4ynh3t_nh4mz3x} with key CRYPTO.",
    hint: "Apply cyclic key shifts backward.",
    hintCost: 40,
    flag: FLAGS.vigenere
  }
];

module.exports = { FLAGS, CHALLENGE_SEED, CRYPTO_ENCODED };
