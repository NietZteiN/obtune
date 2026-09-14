using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> numBase, List<List<string>> delta) {
        for (int j = 0; j < delta.Count; j++)
        {
            for (int i = 0; i < numBase.Count; i++)
            {
                if (numBase[i] == delta[j][0])
                {
                    Debug.Assert(delta[j][1] != numBase[i]);
                    numBase[i] = delta[j][1];
                }
            }
        }
        return numBase;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"gloss", (string)"banana", (string)"barn", (string)"lawn"})), (new List<List<string>>())).SequenceEqual((new List<string>(new string[]{(string)"gloss", (string)"banana", (string)"barn", (string)"lawn"}))));
    }

}
