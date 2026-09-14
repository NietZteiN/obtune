using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        int count = text.Count(c => c == text[0]);
        var ls = text.ToCharArray().ToList();
        for (int i = 0; i < count; i++)
        {
            ls.Remove(ls[0]);
        }
        return string.Join("", ls);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((";,,,?")).Equals((",,,?")));
    }

}
