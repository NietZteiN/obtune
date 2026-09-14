using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string phrase) {
        string result = "";
        foreach (char i in phrase)
        {
            if (!char.IsLower(i))
            {
                result += i;
            }
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("serjgpoDFdbcA.")).Equals(("DFA.")));
    }

}
