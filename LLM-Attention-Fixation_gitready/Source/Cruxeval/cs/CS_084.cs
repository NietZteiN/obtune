using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string[] arr = text.Split(' ');
        List<string> result = new List<string>();
        foreach (string item in arr)
        {
            if (item.EndsWith("day"))
            {
                result.Add(item + "y");
            }
            else
            {
                result.Add(item + "day");
            }
        }
        return string.Join(" ", result);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("nwv mef ofme bdryl")).Equals(("nwvday mefday ofmeday bdrylday")));
    }

}
