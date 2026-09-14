using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<string> names) {
        int count = names.Count;
        int numberOfNames = 0;
        foreach (string name in names) {
            if (name.All(char.IsLetter)) {
                numberOfNames++;
            }
        }
        return numberOfNames;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"sharron", (string)"Savannah", (string)"Mike Cherokee"}))) == (2L));
    }

}
