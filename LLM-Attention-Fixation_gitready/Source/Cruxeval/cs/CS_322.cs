using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> chemicals, long num) {
        List<string> fish = chemicals.GetRange(1, chemicals.Count - 1);
        chemicals.Reverse();
        for (int i = 0; i < num; i++)
        {
            fish.Add(chemicals[1]);
            chemicals.RemoveAt(1);
        }
        chemicals.Reverse();
        return chemicals;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"lsi", (string)"s", (string)"t", (string)"t", (string)"d"})), (0L)).SequenceEqual((new List<string>(new string[]{(string)"lsi", (string)"s", (string)"t", (string)"t", (string)"d"}))));
    }

}
