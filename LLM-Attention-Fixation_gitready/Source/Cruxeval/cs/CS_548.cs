using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string suffix) {
        if (!string.IsNullOrEmpty(suffix) && !string.IsNullOrEmpty(text) && text.EndsWith(suffix)) {
            return text.Remove(text.Length - suffix.Length);
        } else {
            return text;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("spider"), ("ed")).Equals(("spider")));
    }

}
