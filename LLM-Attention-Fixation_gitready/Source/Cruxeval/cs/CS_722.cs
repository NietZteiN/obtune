using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string outText = "";
        for (int i = 0; i < text.Length; i++)
        {
            if (Char.IsUpper(text[i]))
            {
                outText += Char.ToLower(text[i]);
            }
            else
            {
                outText += Char.ToUpper(text[i]);
            }
        }
        return outText;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((",wPzPppdl/")).Equals((",WpZpPPDL/")));
    }

}
