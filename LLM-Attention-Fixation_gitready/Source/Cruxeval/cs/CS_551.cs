using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(Dictionary<string,List<string>> data) {
        List<string> members = new List<string>();
        foreach(var item in data)
        {
            foreach(var member in item.Value)
            {
                if (!members.Contains(member))
                {
                    members.Add(member);
                }
            }
        }
        return members.OrderBy(x => x).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,List<string>>(){{"inf", new List<string>(new string[]{(string)"a", (string)"b"})}, {"a", new List<string>(new string[]{(string)"inf", (string)"c"})}, {"d", new List<string>(new string[]{(string)"inf"})}})).SequenceEqual((new List<string>(new string[]{(string)"a", (string)"b", (string)"c", (string)"inf"}))));
    }

}
