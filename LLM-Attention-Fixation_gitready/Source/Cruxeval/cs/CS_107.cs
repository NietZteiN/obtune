using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        List<char> result = new List<char>();
        for (int i = 0; i < text.Length; i++)
        {
            if (!char.IsLetterOrDigit(text[i]))
            {
                return "False";
            }
            else if (char.IsLetterOrDigit(text[i]) && !char.IsWhiteSpace(text[i]))
            {
                result.Add(char.ToUpper(text[i]));
            }
            else
            {
                result.Add(text[i]);
            }
        }
        return new string(result.ToArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ua6hajq")).Equals(("UA6HAJQ")));
    }

}
