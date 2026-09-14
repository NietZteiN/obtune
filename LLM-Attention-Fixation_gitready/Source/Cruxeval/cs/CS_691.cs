using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string suffix) {
        if (!string.IsNullOrEmpty(suffix) && text.Contains(suffix[suffix.Length - 1].ToString())) {
            return F(text.TrimEnd(suffix[suffix.Length - 1]), suffix.Substring(0, suffix.Length - 1));
        } else {
            return text;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("rpyttc"), ("cyt")).Equals(("rpytt")));
    }

}
