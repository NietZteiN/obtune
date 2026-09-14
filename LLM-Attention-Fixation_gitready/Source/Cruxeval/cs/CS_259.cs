using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        List<char> newText = new List<char>();
        foreach (char character in text)
        {
            if (char.IsUpper(character))
            {
                newText.Insert(newText.Count / 2, character);
            }
        }
        if (newText.Count == 0)
        {
            newText.Add('-');
        }
        return string.Join("", newText);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("String matching is a big part of RexEx library.")).Equals(("RES")));
    }

}
