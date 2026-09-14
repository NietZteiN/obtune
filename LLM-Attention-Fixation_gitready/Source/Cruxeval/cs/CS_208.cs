using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> items) {
        List<string> result = new List<string>();
        foreach(var item in items) {
            foreach(var d in item) {
                if (!char.IsDigit(d)) {
                    result.Add(d.ToString());
                }
            }
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"123", (string)"cat", (string)"d dee"}))).SequenceEqual((new List<string>(new string[]{(string)"c", (string)"a", (string)"t", (string)"d", (string)" ", (string)"d", (string)"e", (string)"e"}))));
    }

}
