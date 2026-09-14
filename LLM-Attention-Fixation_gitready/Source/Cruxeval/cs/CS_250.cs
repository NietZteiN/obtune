using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        int count = text.Length;
        for (int i = -count + 1; i < 0; i++) {
            text = text + text[text.Length + i];
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("wlace A")).Equals(("wlace Alc l  ")));
    }

}
