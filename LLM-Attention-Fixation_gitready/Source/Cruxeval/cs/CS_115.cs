using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        List<byte[]> res = new List<byte[]>();
        byte[] encoded = Encoding.UTF8.GetBytes(text);
        foreach(var ch in encoded)
        {
            if (ch == 61)
            {
                break;
            }
            if (ch == 0)
            {
                continue;
            }
            res.Add(Encoding.UTF8.GetBytes($"{ch}; "));
        }
        return "b'" + string.Join("", res.Select(x => Encoding.UTF8.GetString(x))) + "'";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("os||agx5")).Equals(("b'111; 115; 124; 124; 97; 103; 120; 53; '")));
    }

}
