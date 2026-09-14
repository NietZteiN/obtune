using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string c) {
        List<char> ls = text.ToList();
        if (!text.Contains(c)) {
            throw new ArgumentException($"Text has no {c}");
        }
        ls.RemoveAt(text.LastIndexOf(c));
        return string.Join("", ls);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("uufhl"), ("l")).Equals(("uufh")));
    }

}
