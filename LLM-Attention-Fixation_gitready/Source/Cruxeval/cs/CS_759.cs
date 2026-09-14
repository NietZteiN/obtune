using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(string text, string sub) {
        List<long> index = new List<long>();
        int starting = 0;
        while (starting != -1)
        {
            starting = text.IndexOf(sub, starting);
            if (starting != -1)
            {
                index.Add(starting);
                starting += sub.Length;
            }
        }
        return index;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("egmdartoa"), ("good")).SequenceEqual((new List<long>())));
    }

}
