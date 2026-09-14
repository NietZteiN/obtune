using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<string, string> F(Dictionary<string,long> c, long st, long ed) {
        Dictionary<long, string> d = new Dictionary<long, string>();
        long a = 0, b = 0;
        foreach(var pair in c)
        {
            d[pair.Value] = pair.Key;
            if (pair.Value == st)
            {
                a = pair.Value;
            }
            if (pair.Value == ed)
            {
                b = pair.Value;
            }
        }
        string w = d[st];
        return (a > b) ? Tuple.Create(w, d[ed]) : Tuple.Create(d[ed], w);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,long>(){{"TEXT", 7L}, {"CODE", 3L}}), (7L), (3L)).Equals((Tuple.Create("TEXT", "CODE"))));
    }

}
