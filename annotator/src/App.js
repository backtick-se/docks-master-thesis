import { useState } from 'react'
import data from './data.json'
import styled from 'styled-components'
import ReactMarkdown from 'react-markdown'
import rehypeRaw from 'rehype-raw'

const Wrapper = styled('div')`
    display: flex;
    width: 100vw;
    height: 100vh;
    flex-direction: column;
    overflow: hidden;
`

const Foot = styled('div')`
    display: flex;
    justify-content: center;
    padding: 1rem;
`

const Content = styled('div')`
    display: flex;
    flex-grow: 1;
    overflow: hidden;
`

const Section = styled('div')`
    display: flex;
    flex-grow: 1;
    padding: 1rem;
    overflow-y: scroll;
`

const Stats = styled(Section)`
    flex-direction: column;
`

const Features = styled(Section)`
    flex-direction: column;
    width: 30%;
`

const Labels = styled(Section)`
    flex-direction: column;
    width: 30%;
`

const LabelHead = styled('div')`
    display: flex;
    justify-content: space-between;
`

const Commit = styled('span')`
    display: flex;
    flex-direction: column;
    border: solid 1px rgba(0, 0, 0, 0.2);
    padding: 1rem;
    margin-bottom: 0.4rem;
`

const App = () => {
    const [current, setCurrent] = useState(0)
    const [accepted, setAccepted] = useState([])
    const [rejected, setRejected] = useState([])
    const [docpage, setDocpage] = useState(0)
    const [selected, setSelected] = useState([])

    const next = () => {
        setCurrent(current + 1)
    }

    const onSave = () => {
        const fileData = JSON.stringify(accepted)
        const blob = new Blob([fileData], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.download = 'filename.json'
        link.href = url
        link.click()
    }

    const onAccept = () => {
        console.log(data[current])
        setAccepted([{ ...data[current], target: selected }, ...accepted])
        setDocpage(0)
        setSelected([])
        next()
    }

    const onReject = () => {
        setDocpage(0)
        setRejected([data[current], ...rejected])
        setSelected([])
        next()
    }

    const onNextDoc = () => {
        if (docpage + 1 < data[current].docs.length) {
            setDocpage(docpage + 1)
        }
    }

    const onPrevDoc = () => {
        if (docpage > 0) {
            setDocpage(docpage - 1)
        }
    }

    const onRadioChange = (e) => {
        if (selected.includes(data[current].docs[docpage][0])) {
            setSelected(
                selected.filter((s) => s !== data[current].docs[docpage][0])
            )
        } else {
            setSelected([...selected, data[current].docs[docpage][0]])
        }
    }

    return (
        <Wrapper>
            <Content>
                <Stats>
                    <span>
                        <b>Accepted:</b> {accepted.length}
                    </span>
                    <span>
                        <b>Rejected:</b> {rejected.length}
                    </span>
                    <div style={{ flexGrow: 1 }} />
                    <button onClick={onSave}>Save</button>
                </Stats>
                {data[current] && (
                    <>
                        <Features>
                            <LabelHead>
                                <span>{data[current].number}</span>
                                <span>
                                    {current + 1} / {data.length}
                                </span>
                            </LabelHead>
                            <h1>{data[current].title}</h1>
                            <ReactMarkdown rehypePlugins={[rehypeRaw]}>
                                {data[current].body}
                            </ReactMarkdown>
                            <h2>Commits:</h2>
                            {data[current].commits.map((commit, i) => (
                                <>
                                    <Commit>
                                        <LabelHead>
                                            <b>{commit.commit.message}</b>
                                            <b
                                                style={{ whiteSpace: 'nowrap' }}
                                            >{`+${commit.stats['additions']} -${commit.stats['deletions']}`}</b>
                                        </LabelHead>
                                        <br />
                                        {commit.files.map(({ filename }) => (
                                            <>
                                                <i>{filename}</i>
                                                <br />
                                            </>
                                        ))}
                                    </Commit>
                                </>
                            ))}
                        </Features>
                        <Labels>
                            <LabelHead>
                                <span>
                                    <input
                                        type="radio"
                                        name="docpage"
                                        checked={selected.includes(
                                            data[current].docs[docpage][0]
                                        )}
                                        onClick={onRadioChange}
                                        value={docpage}
                                    />
                                </span>
                                <span>
                                    <button onClick={onPrevDoc}>Prev</button>
                                    &nbsp;
                                    <button onClick={onNextDoc}>Next</button>
                                </span>
                                <span>
                                    {docpage} / {data[current].docs.length - 1}
                                </span>
                            </LabelHead>
                            <br />
                            {selected.map((s) => (
                                <span>
                                    <b>Selected:</b> {s}
                                </span>
                            ))}
                            <br />
                            <LabelHead>
                                <span>
                                    <b>Current:</b>{' '}
                                    {data[current].docs[docpage][0]}
                                </span>
                            </LabelHead>
                            <ReactMarkdown>
                                {data[current].docs[docpage][1]}
                            </ReactMarkdown>
                        </Labels>
                    </>
                )}
            </Content>
            <Foot>
                <button onClick={onReject}>Reject Datapoint</button>
                &nbsp;
                <button onClick={onAccept}>Accept Selection</button>
            </Foot>
        </Wrapper>
    )
}

export default App
