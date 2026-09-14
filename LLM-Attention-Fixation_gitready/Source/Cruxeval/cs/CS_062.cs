using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<string, string, string, string> F(Dictionary<string,string> user) {
        if (user.Keys.Count() > user.Values.Count())
        {
            return Tuple.Create(user.Keys.ToArray()[0], user.Keys.ToArray()[1], user.Keys.ToArray()[2], user.Keys.ToArray()[3]);
        }
        else
        {
            return Tuple.Create(user.Values.ToArray()[0], user.Values.ToArray()[1], user.Values.ToArray()[2], user.Values.ToArray()[3]);
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,string>(){{"eating", "ja"}, {"books", "nee"}, {"piano", "coke"}, {"excitement", "zoo"}})).Equals((Tuple.Create("ja", "nee", "coke", "zoo"))));
    }

}
