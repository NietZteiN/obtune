using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string body) {
        char[] ls = body.ToCharArray();
        int dist = 0;
        StringBuilder s = new StringBuilder();
        for(int i = 0; i < ls.Length - 1; i++)
        {
            if(i - 2 >= 0 && ls[i - 2] == '\t')
            {
                dist += (1 + new string(ls[i - 1], 1).Count(c => c == '\t')) * 3;
            }
            s.Append('[').Append(ls[i]).Append(']');
        }
        s.Append(ls[ls.Length - 1]);
        return s.ToString().Replace("\t", new string(' ', dist + 4));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("\n\ny\n")).Equals(("[\n][\n][y]\n")));
    }

}
