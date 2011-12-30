
todo = [{'cp': True, 'id': '55f81932-4a7e-acfb-6ce3-e72796bda868', 'nm': 'notsobad'},
 {'cp': True, 'id': 'd83a7b8f-b2d8-938c-39fd-76a57a9a99d6', 'nm': 'test'},
 {'id': '614ed58d-cdef-a2a7-a22f-b8c2d0718e3d', 'nm': 'abc'},
 {'ch': [{'ch': [{'ch': [{'ch': [{'id': '15b8681c-5873-3520-9163-958a213efe1b',
                                  'nm': 'go home'},
                                 {'id': 'aab678c8-2918-78ba-db8c-d7b6a600e20f',
                                  'nm': 'aaaa'},
                                 {'id': 'f50d117d-753a-83ef-0332-e81b9161a63c',
                                  'nm': ''}],
                          'id': '608925d3-5f80-fb2e-0140-c7a479e1e2ad',
                          'nm': 'aasdfa'},
                         {'cp': True,
                          'id': '6bad20c8-6bf5-0ce6-8af4-34ab3199385f',
                          'nm': 'sss'},
                         {'cp': True,
                          'id': 'da0bccd9-eb02-3d8d-276c-13670f5c6f7c',
                          'nm': 'asdfasdf'}],
                  'cp': True,
                  'id': '32dfbbc8-b561-1b05-729f-2c2e7501bde1',
                  'nm': 'aaaa'},
                 {'id': '7ad06e5e-f278-176e-3cf8-384ae787100b',
                  'nm': 'aaaaaa'}],
          'id': '96ce59ae-5f7c-5f2a-d1ca-5a0a45e3198a',
          'nm': 'test'}],
  'id': '9bb718b1-a755-cace-6e06-2e36ab46c495',
  'nm': '18.29'},
 {'id': '909b5b4a-228c-61a4-627f-76cc400df49d', 'nm': 'aaaa'}]


def search(todo, key):
	for t in todo:
		if t['id'] == key:
			print t
			return
		if 'ch' in t:
			search(t['ch'], key)


search(todo, "da0bccd9-eb02-3d8d-276c-13670f5c6f7c")
search(todo, "96ce59ae-5f7c-5f2a-d1ca-5a0a45e3198a")
