using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<string, long> F(string s) {
        long count = 0;
        string digits = "";
        foreach(char c in s)
        {
            if(char.IsDigit(c))
            {
                count += 1;
                digits += c;
            }
        }
        return Tuple.Create(digits, count);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("qwfasgahh329kn12a23")).Equals((Tuple.Create("3291223", 7L))));
    }

}
