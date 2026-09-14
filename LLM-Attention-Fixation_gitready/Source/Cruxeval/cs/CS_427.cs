using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s) {
        int count = s.Length - 1;
        string reverseS = new string(s.Reverse().ToArray());
        while (count > 0 && reverseS.Where((c, i) => i % 2 == 0).ToArray().ToString().IndexOf("sea") == -1)
        {
            count--;
            reverseS = new string(reverseS.Take(count).ToArray());
        }
        return new string(reverseS.Skip(count).ToArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("s a a b s d s a a s a a")).Equals(("")));
    }

}
