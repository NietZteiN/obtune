using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str) {
        if (str.All(char.IsLetterOrDigit))
        {
            return "ascii encoded is allowed for this language";
        }
        return "more than ASCII";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Str zahrnuje anglo-ameriæske vasi piscina and kuca!")).Equals(("more than ASCII")));
    }

}
