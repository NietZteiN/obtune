using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string suffix) {
        if (text.EndsWith(suffix))
        {
            text = text.Substring(0, text.Length - 1) + char.ToUpper(text[text.Length - 1]);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("damdrodm"), ("m")).Equals(("damdrodM")));
    }

}
