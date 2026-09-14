using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        int index = 1;
        while (index < text.Length){
            if (text[index] != text[index - 1]) {
                index += 1;
            } else {
                string text1 = text.Substring(0,index);
                string text2 = new string((from c in text.Substring(index) select Char.IsUpper(c) ? Char.ToLower(c) : Char.ToUpper(c)).ToArray());
                return text1 + text2;
            }
        }
        return new string((from c in text select Char.IsUpper(c) ? Char.ToLower(c) : Char.ToUpper(c)).ToArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("USaR")).Equals(("usAr")));
    }

}
