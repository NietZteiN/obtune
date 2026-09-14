using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string newText = text;
        while (text.Length > 1 && text[0] == text[text.Length - 1]) {
            newText = text = text.Substring(1, text.Length - 2);
        }
        return newText;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((")")).Equals((")")));
    }

}
