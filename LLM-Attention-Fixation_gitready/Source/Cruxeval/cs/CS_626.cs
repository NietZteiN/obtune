using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string line, List<Tuple<string, string>> equalityMap) {
        Dictionary<char, char> rs = equalityMap.ToDictionary(t => t.Item1[0], t => t.Item2[0]);
        return line.Aggregate(new StringBuilder(), (sb, c) => {
            sb.Append(rs.ContainsKey(c) ? rs[c] : c);
            return sb;
        }).ToString();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abab"), (new List<Tuple<string, string>>(new Tuple<string, string>[]{(Tuple<string, string>)Tuple.Create("a", "b"), (Tuple<string, string>)Tuple.Create("b", "a")}))).Equals(("baba")));
    }

}
