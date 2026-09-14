using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<string, string> F(string s) {
        if (s.Length >= 5 && s.Substring(s.Length - 5).All(c => c <= 127))
        {
            return new Tuple<string, string>(s.Substring(s.Length - 5), s.Substring(0, 3));
        }
        else if (s.Length >= 5 && s.Substring(0, 5).All(c => c <= 127))
        {
            return new Tuple<string, string>(s.Substring(0, 5), s.Substring(s.Length - 2));
        }
        else
        {
            return new Tuple<string, string>(s, null);
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("a1234år")).Equals((Tuple.Create("a1234", "år"))));
    }

}
