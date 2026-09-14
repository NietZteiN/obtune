using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string strip_chars) {
        char[] charArray = text.ToCharArray();
        Array.Reverse(charArray);
        string reversedText = new string(charArray);
        string strippedText = reversedText.Trim(strip_chars.ToCharArray());
        charArray = strippedText.ToCharArray();
        Array.Reverse(charArray);
        return new string(charArray);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("tcmfsmj"), ("cfj")).Equals(("tcmfsm")));
    }

}
