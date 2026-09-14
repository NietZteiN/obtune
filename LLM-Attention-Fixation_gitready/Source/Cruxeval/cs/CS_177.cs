using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        char[] charArray = text.ToCharArray();
        for (int i = 0; i < charArray.Length; i++) {
            if (i % 2 == 1) {
                charArray[i] = char.IsUpper(charArray[i]) ? char.ToLower(charArray[i]) : char.ToUpper(charArray[i]);
            }
        }
        return new string(charArray);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Hey DUdE THis $nd^ &*&this@#")).Equals(("HEy Dude tHIs $Nd^ &*&tHiS@#")));
    }

}
