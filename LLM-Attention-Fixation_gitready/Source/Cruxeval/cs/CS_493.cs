using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(Dictionary<string,string> d) {
        List<string> keys = new List<string>();
        foreach(var k in d.Keys) {
            keys.Add(string.Format("{0} => {1}", k, d[k]));
        }
        return keys;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,string>(){{"-4", "4"}, {"1", "2"}, {"-", "-3"}})).SequenceEqual((new List<string>(new string[]{(string)"-4 => 4", (string)"1 => 2", (string)"- => -3"}))));
    }

}
