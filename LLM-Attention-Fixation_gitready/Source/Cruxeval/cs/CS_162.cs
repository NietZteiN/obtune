using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string result = "";
        foreach (char c in text)
        {
            if (char.IsLetterOrDigit(c))
            {
                result += char.ToUpper(c);
            }
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("с bishop.Swift")).Equals(("СBISHOPSWIFT")));
    }

}
