using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static string F(string text, string character) {
        if (!string.IsNullOrEmpty(text))
        {
            text = text.StartsWith(character) ? text.Substring(character.Length) : text;
            text = text.StartsWith(text[text.Length - 1].ToString()) ? text.Substring(0, text.Length - 1) : text;
            text = text.Substring(0, text.Length - 1) + char.ToUpper(text[text.Length - 1]);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("querist"), ("u")).Equals(("querisT")));
    }

}
