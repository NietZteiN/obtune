using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(Dictionary<string,long> d) {
        List<string> l = new List<string>();
        while(d.Count > 0)
        {
            KeyValuePair<string, long> last = d.Last();
            d.Remove(last.Key);
            l.Add(last.Key);
        }
        return l;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,long>(){{"f", 1L}, {"h", 2L}, {"j", 3L}, {"k", 4L}})).SequenceEqual((new List<string>(new string[]{(string)"k", (string)"j", (string)"h", (string)"f"}))));
    }

}
