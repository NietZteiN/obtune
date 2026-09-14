using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text, string pref) {
        if (pref.GetType() == typeof(List<string>))
        {
            string result = string.Join(", ", pref.Select(x => text.StartsWith(x).ToString()));
            return bool.Parse(result);
        }
        else
        {
            return text.StartsWith(pref);
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Hello World"), ("W")) == (false));
    }

}
