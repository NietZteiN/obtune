using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string letters) {
        string lettersOnly = letters.TrimEnd(new char[] { '.', ',', ' ', '!', '?', '*' });
        return string.Join("....", lettersOnly.Split(' '));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("h,e,l,l,o,wo,r,ld,")).Equals(("h,e,l,l,o,wo,r,ld")));
    }

}
