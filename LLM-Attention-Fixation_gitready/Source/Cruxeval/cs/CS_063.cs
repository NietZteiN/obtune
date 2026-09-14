using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string prefix) {
        while(text.StartsWith(prefix)) {
            text = text.Substring(prefix.Length) == "" ? text : text.Substring(prefix.Length);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ndbtdabdahesyehu"), ("n")).Equals(("dbtdabdahesyehu")));
    }

}
