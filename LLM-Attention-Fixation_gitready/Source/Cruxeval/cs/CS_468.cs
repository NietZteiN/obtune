using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string a, string b, long n) {
        string result = b;
        string m = b;
        for (int i = 0; i < n; i++)
        {
            if (m != null)
            {
                a = a.Replace(m, "");
                m = null;
                result = b;
            }
        }
        return String.Join(result, a.Split(b.ToArray()));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("unrndqafi"), ("c"), (2L)).Equals(("unrndqafi")));
    }

}
