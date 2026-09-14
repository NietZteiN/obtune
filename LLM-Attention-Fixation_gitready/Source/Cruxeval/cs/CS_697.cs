using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<string, string, string> F(string s, string sep) {
        int sep_index = s.IndexOf(sep);
        string prefix = s.Substring(0, sep_index);
        string middle = s.Substring(sep_index, sep.Length);
        string right_str = s.Substring(sep_index + sep.Length);
        return Tuple.Create(prefix, middle, right_str);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("not it"), ("")).Equals((Tuple.Create("", "", "not it"))));
    }

}
